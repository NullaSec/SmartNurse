import React from 'react';
import PatientCard from './PatientCard';
import { Grid } from '@mui/material';

const PatientList = ({ patients }) => {
  return (
    <Grid container spacing={2}>
      {patients.map((patient) => (
        <Grid item xs={12} md={6} lg={4} key={patient.id}>
          <PatientCard patient={patient} />
        </Grid>
      ))}
    </Grid>
  );
};

export default PatientList;
