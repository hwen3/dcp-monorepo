import React from 'react';
import { useEffect } from 'react';
import {
  GoAMicrositeHeader,
  GoAAppHeader,
} from '@abgov/react-components';

const Header = () => {
  useEffect(() => {
    if (
      window.location.hostname ===
        'common-capabilities-dcp-uat.apps.aro.gov.ab.ca' ||
      window.location.hostname === 'common-capabilities.digital.gov.ab.ca'
    ) {
      globalThis.adspFeedback?.initialize?.({
        tenant: 'common_capabilities',
      });
    }
  });

  return (
    <>
      <GoAMicrositeHeader type="live" maxContentWidth="1500px" />
      <GoAAppHeader
        url="/"
        heading="Common capabilities"
        maxContentWidth="1500px"
      >
        <a href="/gettingstarted/index.html#getting-started">Getting started</a>
        <a href="/about/index.html">About</a>
        <a href="/ecosystem/index.html">Eco-system</a>
        <a href="/services/index.html">Services</a>
        <a href="/support/index.html">Support</a>
      </GoAAppHeader>
    </>
  );
};

export default Header;
