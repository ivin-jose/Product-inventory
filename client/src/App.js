import React, { useEffect, useState } from 'react';


function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('/Model/auth_user')
      .then(res => res.json())
      .then(data => setData(data))
      // .catch(error => console.error('Error fetching data:', error));
  }, []); // Dependency array added

  return (
    <div>
      {typeof data.members != 'undefined' ? (
        <p>Loading...</p>
      ) : (
        data.members.map((member, i) => (
          <p key={i}>{member}</p>
        ))
      )}
    </div>
  );
  
}

export default App;

