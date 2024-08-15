import React from 'react';
import ReactDOM from 'react-dom';
import ServerDropdown from './ServerDropdown';

window.React = React;
window.ReactDOM = ReactDOM;
window.ServerDropdown = ServerDropdown;

console.log("React components loaded");

document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM content loaded");
  const serverDropdownContainer = document.getElementById('server-dropdown');
  if (serverDropdownContainer) {
    const accessToken = serverDropdownContainer.getAttribute('data-access-token');
    ReactDOM.render(
      <ServerDropdown accessToken={accessToken} />,
      serverDropdownContainer
    );
  } else {
    console.error("Server dropdown container not found");
  }
});