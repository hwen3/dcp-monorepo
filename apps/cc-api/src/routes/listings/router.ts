import { TokenProvider } from '@abgov/adsp-service-sdk';
import { RequestHandler, Router } from 'express';
import { Logger } from 'winston';
import axios from 'axios';
import { getService, getServices } from './services';
import { DataCache } from '../../cache/types';
import { SiteVerifyResponse } from './types';
import { v4 as uuidv4, validate as uuidValidate } from 'uuid';
import { environment } from '../../environments/environment';

interface RouterOptions {
  logger: Logger;
  tokenProvider: TokenProvider;
  formApiUrl: URL;
  eventServiceUrl: URL;
  valueServiceUrl: URL;
  cache: DataCache;
}

export function verifyCaptcha(logger: Logger, RECAPTCHA_SECRET: string, SCORE_THRESHOLD = 0.5): RequestHandler {
  return async (req, _res, next) => {
    if (!RECAPTCHA_SECRET) {
      next();
    } else {
      try {
        const { captchaToken } = req.body;
        const { data } = await axios.post<SiteVerifyResponse>(
          `https://www.google.com/recaptcha/api/siteverify?secret=${RECAPTCHA_SECRET}&response=${captchaToken}`
        );
        console.log(data);

        if (!data.success || !['submit'].includes(data.action) || data.score < SCORE_THRESHOLD) {
          logger.warn(
            `Captcha verification failed for form gateway with result '${data.success}' on action '${data.action}' with score ${data.score}.`,
            { context: 'DigitalMarketplace' }
          );

          return _res.status(401).send('Request rejected because captcha verification not successful.');
        }

        next();
      } catch (err) {
        next(err);
      }
    }
  };
}

export function getFormsSchema(
  logger: Logger,
  formApiUrl: URL,
  tokenProvider: TokenProvider
): RequestHandler {
  return async (req, res) => {

    try {
      const token = await tokenProvider.getAccessToken();
      const { definitionId } = req.params;

      const getFormsSchemaData = await axios.get(
        `${formApiUrl}/definitions/${definitionId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      res.status(200).send({
        dataSchema: getFormsSchemaData.data.dataSchema,
        uiSchema: getFormsSchemaData.data.uiSchema
      });
    } catch (e) {
      if (axios.isAxiosError(e)) {
        res.status(e.response.status).send(e.response.data);
        logger.error(e.response.data, 'failed to get forms schema');
      } else {
        res.status(400).send({ error: e });
        logger.error(e, 'failed to get forms schema');
      }
    }

  }
}

export function newListing(
  logger: Logger,
  formApiUrl: URL,
  eventServiceUrl: URL,
  tokenProvider: TokenProvider
): RequestHandler {

  return async (req, res) => {

    try {
      const token = await tokenProvider.getAccessToken();
      const requestBody = req.body;

      // Submit the listing for review
      const listingApiCall = await axios.post(
        `${formApiUrl}/forms`,
        {
          definitionId: 'common-capabilities-intake',
          data: {
            ...requestBody.formData,
            appId: (!requestBody.formData.appId || !uuidValidate(requestBody.formData.appId))
              ? uuidv4()
              : requestBody.formData.appId,
          },
          submit: true
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (listingApiCall.data.status === 'submitted') {
        try {
          // Notify the user about their submission
          await axios.post(`${eventServiceUrl}/events`, {
            "namespace": "common-capabilities",
            "name": requestBody.formData.appId ? "listing-submitted-edit" : "listing-submitted-new",
            "timestamp": new Date().toISOString(),
            "payload": {
              "userEmail": requestBody.formData.editorEmail,
              appName: requestBody.formData.serviceName,
              userName: requestBody.formData.editorName
            }
          }, {
            headers: {
              Authorization: `Bearer ${token}`,
            }
          })
          const reviewerEmails = environment.REVIEWER_EMAILS.split(",");

          // Notify the reviewers
          await Promise.all(
            reviewerEmails.map(
              (reviewerEmail) =>
                axios.post(`${eventServiceUrl}/events`, {
                  "namespace": "common-capabilities",
                  "name": requestBody.formData.appId ? "listing-submitted-edit-reviewer" : "listing-submitted-new-reviewer",
                  "timestamp": new Date().toISOString(),
                  "payload": {
                    "userEmail": reviewerEmail,
                    appName: requestBody.formData.serviceName,
                    userName: requestBody.formData.editorName,
                    editorEmail: requestBody.formData.editorEmail
                  }
                }, {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  }
                })
            )
          );
        } catch (e) {
          if (axios.isAxiosError(e)) {
            res.status(e.response.status).send(e.response.data);
            logger.error(e.response.data, 'failed to notify reviewers');
          } else {
            res.status(400).send({ error: e });
            logger.error(e, 'failed to notify reviewers');
          }
        }
      }
      res.status(201).send({
        result: {
          id: listingApiCall.data.id,
          status: listingApiCall.data.status,
        },
      });
    }
    catch (e) {
      if (axios.isAxiosError(e)) {
        res.status(e.response.status).send(e.response.data);
        logger.error(e.response.data, 'failed to get forms schema');
      } else {
        res.status(400).send({ error: e });
        logger.error(e, 'failed to get forms schema');
      }
    }
  }
}

function clearCache(cache: DataCache): RequestHandler {
  return async (req, res) => {
    await cache.clear();
    res.status(200).send();
  }
}

export function createListingsRouter({
  logger,
  tokenProvider,
  formApiUrl,
  valueServiceUrl,
  eventServiceUrl,
  cache,
}: RouterOptions): Router {
  const router = Router();

  router.get(
    '/listings/schema/:definitionId',
    getFormsSchema(logger, formApiUrl, tokenProvider)
  );

  router.post(
    '/listings',
    verifyCaptcha(logger, environment.RECAPTCHA_SECRET, 0.7),
    newListing(logger, formApiUrl, eventServiceUrl, tokenProvider)
  );

  router.get(
    '/listings/services',
    getServices(logger, valueServiceUrl, tokenProvider, cache)
  );

  router.get(
    '/listings/services/:serviceId',
    getService(logger, valueServiceUrl, tokenProvider, cache)
  );

  router.post('/cache/clear', clearCache(cache));

  return router;
}
