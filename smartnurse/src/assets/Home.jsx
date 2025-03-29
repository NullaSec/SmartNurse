import React from 'react';
import Header from '../components/Header';
import PatientList from '../components/PatientList';
import { Container } from '@mui/material';

const Home = ({ patients }) => {
  return (
    <div>
      <Header />
      <Container>
        <h2>Patient List</h2>
        <PatientList patients={patients} />
      </Container>
    </div>
  );
};

export default Home;
