import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';

console.log(process.env.REACT_APP_API)

ReactDOM.render(
  <App />,
  document.getElementById('root')
);
