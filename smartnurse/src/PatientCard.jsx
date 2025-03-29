import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

const PatientCard = ({ patient }) => {
  return (
    <Card sx={{ minWidth: 275, marginBottom: 2 }}>
      <CardContent>
        <Typography variant="h6">{patient.name}</Typography>
        <Typography color="textSecondary">Allergies: {patient.allergies.join(", ")}</Typography>
        <Typography color="textSecondary">Next appointment: {patient.nextAppointment}</Typography>
      </CardContent>
    </Card>
  );
};

export default PatientCard;
