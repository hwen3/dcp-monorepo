function domanin() {
    switch(window.location.hostname.toLowerCase()) {
        case 'digitalmarketplace.alberta.ca':
          return 'PROD';

        case 'digital-marketplace-dcp-uat.apps.aro.gov.ab.ca':
          return 'UAT';

        default:
          return "?";
      }    
}

export function getFeedbackUrl() {
    if (domanin() == 'PROD') {
        return 'https://feedback-service.adsp.alberta.ca/feedback/v1/script/adspFeedback.js';
      
    } else {
        return 'https://feedback-service.adsp-uat.alberta.ca/feedback/v1/script/adspFeedback.js'; 
    }
}

export function getGoogle() {
    switch(domanin()) {
        case 'PROD':  return 'G-95TDFJFW58';
        case 'UAT':   return 'G-MEL64N8Q28';
        default:      return "?";   // first character == "?" will disable
      }
}