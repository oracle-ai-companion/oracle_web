import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styles from './ServerDropdown.module.css';

const ServerDropdown = ({ accessToken }) => {
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchServers = async () => {
      try {
        const response = await axios.get('/api/get_user_servers', {
          params: { access_token: accessToken }
        });
        setServers(response.data);
      } catch (error) {
        console.error('Error fetching servers:', error);
        setError('Failed to fetch servers. Please try again later.');
      }
    };

    if (accessToken) {
      fetchServers();
    } else {
      setError('No access token available.');
    }
  }, [accessToken]);

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  const toggleDropdown = () => {
    console.log("Toggling dropdown");
    setIsOpen(!isOpen);
  };

  const handleServerSelect = (server) => {
    setSelectedServer(server);
    setIsOpen(false);
  };

  return (
    <div className={styles.serverDropdown}>
      <div className={styles.dropdownHeader} onClick={toggleDropdown}>
        <span>{selectedServer ? selectedServer.name : 'Select a server'}</span>
        <span className={`${styles.dropdownArrow} ${isOpen ? styles.dropdownArrowOpen : ''}`}>▼</span>
      </div>
      {isOpen && (
        <ul className={styles.serverList}>
          {servers.map((server) => (
            <li
              key={server.id}
              className={styles.serverItem}
              onClick={() => handleServerSelect(server)}
            >
              {server.icon && (
                <img
                  src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png`}
                  alt={`${server.name} icon`}
                  className={styles.serverIcon}
                />
              )}
              {server.name}
            </li>
          ))}
        </ul>
      )}
      <div>Debug: Component rendered, Servers: {servers.length}</div>
    </div>
  );
};

export default ServerDropdown;