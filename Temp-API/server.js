const express = require("express");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 3000;

const TEMP_PATH = "/sys/class/thermal/thermal_zone0/temp";
let cachedTemperature = null;
let lastUpdateTime = 0;
const CACHE_DURATION = 1000; // 1 second

const updateTemperature = () => {
    try {
        if (fs.existsSync(TEMP_PATH)) {
            const temp = fs.readFileSync(TEMP_PATH, "utf8").trim();
            cachedTemperature = parseFloat(temp) / 1000;
            lastUpdateTime = Date.now();
        } else {
            throw new Error("Temperature file not found");
        }
    } catch (error) {
        console.error("Error reading CPU temperature:", error);
        cachedTemperature = null;
    }
};

// Periodically update temperature
setInterval(updateTemperature, CACHE_DURATION);
updateTemperature(); // Initial read

app.get("/cpu-temperature", (req, res) => {
    if (cachedTemperature === null) {
        return res.status(500).json({ error: "Failed to retrieve CPU temperature" });
    }
    res.json({ temperature: cachedTemperature });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
