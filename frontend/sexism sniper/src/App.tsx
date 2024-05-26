import { useEffect, useState } from "react";
import reactLogo from "./assets/react.svg";
// import viteLogo from '/vite.svg'
import "./App.css";

function App() {
  // obtain the worst offender from the database, this is their picture URL
  const [worstOffender, setWorstOffender] = useState("");

  // make api call to get worst offender
  useEffect(() => {
    fetch("http://localhost:3000/topScore")
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        setWorstOffender(data.url);
      });
  }, []);

  return (
    <>
      <h1>Sexism Sniper</h1>

      <h2>Public Enemy #1</h2>

      {/* access database to find person with most red flags, place person's face here */}
      <img
        src={worstOffender.length > 0 ? worstOffender : reactLogo}
        alt="Wanted Dead or Alive"
      />

      <div className="card">
        {/* calculate bounty based on number of red flags */}
        <h3>Bounty: $100</h3>
        {/* link to casey's venmo */}
        <button>Pay Your Bounty</button>
      </div>
    </>
  );
}

export default App;

{
  /* <button onClick={() => setCount((count) => count + 1)}> count is {count}</button> */
}
