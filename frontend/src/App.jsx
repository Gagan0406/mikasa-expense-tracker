import React from 'react';
import { Routes, Route, Outlet } from 'react-router-dom'; 

import LoginComponent from './components/LogInComponent';
import RegisterComponent from './components/RegisterComponent';
import Navbar from './components/Navbar';
import ProtectedRoute from './pages/ProtectedRoute';
import DashboardPage from './pages/DashboardPage';
import VerifyAccountPage from './pages/VerifyAccountPage';
import EmailVerificationPage from './pages/EmailVerificationPage'; 


const ProtectedLayout = () => {
  return (
    <>
      <Navbar />
      <main className="w-full bg-gray-900 text-white p-4">
        <div className="max-w-7xl mx-auto pt-16"> 
           <Outlet /> 
        </div>
      </main>
    </>
  );
};

const TransactionsPage = () => (
  <div>
    <h1 className="text-3xl font-bold">Transactions</h1>
    <p className="mt-4 text-slate-400">Your transaction history will be displayed here.</p>
  </div>
);


function App() {
  return (
    <Routes>
 
      <Route path="/login" element={<LoginComponent />} />
      <Route path="/register" element={<RegisterComponent />} />
      <Route path="/verify-email" element={<EmailVerificationPage />} />


      <Route element={<ProtectedRoute><ProtectedLayout /></ProtectedRoute>}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/transactions" element={<TransactionsPage />} />
      </Route>

      <Route 
        path="/verify-account" 
        element={
          <ProtectedRoute>
            <VerifyAccountPage />
          </ProtectedRoute>
        } 
      />
      
      <Route path="*" element={<div className="w-full min-h-screen bg-gray-900 flex items-center justify-center"><h1 className="text-white text-4xl">404 Not Found</h1></div>} />
    </Routes>
  );
}

export default App;
