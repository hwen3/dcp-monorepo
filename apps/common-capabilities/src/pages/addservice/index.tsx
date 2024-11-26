import React from 'react';
import ServiceFormWrapper from '../../components/ServiceForm/ServiceFormWrapper';
import useForm from '../../hooks/useFormSubmit';
import BackButton from '../../components/BackButton';

export default function AddServicePage() {
  const { handleSubmit } = useForm();

  const backLink = (
    <BackButton
      text="Back to listing"
      onClick={() => {
        history.back();
      }}
    />
  );

  return (
    <ServiceFormWrapper
      backLink={backLink}
      pageHeader="Add Service"
      handleSubmit={handleSubmit}
    />
  );
}
