"use client";

import { Scheduler } from "@aldabil/react-scheduler";
import { ProcessedEvent } from "@aldabil/react-scheduler/types";
import { Fragment, useEffect, useState } from "react";

export default function Home() {
  const [events, setEvents] = useState<ProcessedEvent[]>([]);
  const [inputValue, setInputValue] = useState("1002606885");
  const [responseMessage, setResponseMessage] = useState("");

  const handleSubmit = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/get_power_outage/${inputValue}`
      );
      if (response.ok) {
        const data = await response.json();

        data.forEach((element: any) => {
          const start = new Date(element.start_time_utc);
          const end = new Date(element.end_time_utc);
          const title = "Test";

          setEvents((prevEvents) => [
            ...prevEvents,
            {
              event_id: Math.random(),
              start,
              end,
              title,
            },
          ]);
        });
          
        
      } else {
        setResponseMessage("Error fetching data");
      }
    } catch (error) {
      setResponseMessage(
        "Error: " + (error instanceof Error ? error.message : "Unknown error")
      );
    }
  };

  return (
    <Fragment>
      <div style={{ marginTop: "20px" }}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter text"
        />
        <button onClick={handleSubmit}>Submit</button>
        <p>{responseMessage}</p>
      </div>

      <Scheduler
        view="week"
        events={events}
        editable={false}
        deletable={false}
        draggable={false}
        agenda={false}
        disableViewNavigator={true}
        week={{
          weekDays: [0, 1, 2, 3, 4, 5, 6],
          weekStartOn: 0,
          startHour: 0,
          endHour: 24,
          step: 60,
          navigation: true,
          disableGoToDay: false,
        }}
      />
    </Fragment>
  );
}
