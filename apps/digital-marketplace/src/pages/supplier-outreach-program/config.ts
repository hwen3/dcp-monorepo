import { FormConfig } from "../../contexts/types";

export const apptFormConfig: FormConfig = {
  properties: {
    orgName: {
      required: true,
      messages: {
        required: 'Enter your organization name',
      },
      validate: [
        {
          regEx: /^(.){2,100}$/,
          failed: 'Must be between 2 and 100 characters long',
        },
        {
          regEx: /^[a-zA-Z0-9&.,' -]+$/,
          failed: `Name should use letters, numbers, spaces or &'.,- "`,
        },
      ],
      includedInPayload: true,
    },
    email: {
      required: true,
      messages: {
        required: 'Enter your email address',
      },
      validate: [
        {
          regEx: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
          failed: 'Invalid email address',
        },
      ],
      includedInPayload: true,
    },
    phone: {
      required: true,
      messages: {
        required: 'Enter your phone number',
      },
      validate: [
        {
          regEx: /^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$/,
          failed: 'Enter a valid phone number, including dashes',
        },
      ],
      includedInPayload: true,
    },
    firstName: {
      required: true,
      messages: {
        required: 'Enter your first name',
      },
      validate: [
        {
          regEx: /^(.){2,100}$/,
          failed: 'Must be between 2 and 100 characters long',
        },
        {
          regEx: /^[a-zA-Z0-9' -]+$/,
          failed: `Name should use letters, numbers, spaces`,
        },
      ],
      includedInPayload: true,
    },
    lastName: {
      required: true,
      messages: {
        required: 'Enter your last name',
      },
      validate: [
        {
          regEx: /^(.){2,100}$/,
          failed: 'Must be between 2 and 100 characters long',
        },
        {
          regEx: /^[a-zA-Z0-9' -]+$/,
          failed: `Name should use letters, numbers, spaces`,
        },
      ],
      includedInPayload: true,
    },
    comments: {
      required: true,
      messages: {
        required: 'Describe what you would like to discuss'
      },
      validate: [],
      includedInPayload: true,
    },
    website: {
      required: false,
      messages: {},
      validate: [
        {
          regEx:
            /^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/,
          failed: 'Please check the web address.',
        },
      ],
      includedInPayload: true,
    },
    agreement: {
      required: true,
      messages: {},
      validate: [],
      includedInPayload: true,
    },
    date: {
      required: true,
      messages: {
        required: 'Select a date',
      },
      validate: [],
      includedInPayload: true,
    },
    when: {
      required: true,
      messages: {
        required: 'Select a time slot',
      },
      validate: [],
      includedInPayload: true,
    },
  },
  getEntityUrl: (gatewayUrl: string, values: any) => `${gatewayUrl}/${values}`,
};
