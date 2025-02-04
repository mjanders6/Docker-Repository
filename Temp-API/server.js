const express = require("express");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 3000;

const TEMP_PATH = "/sys/class/thermal/thermal_zone0/temp";
let cachedTemperature = null;
let lastUpdateTime = 0;
const CACHE_DURATION = 1000; // 1 second

// Function to read CPU temperature
const getCpuTemperature = () => {
    try {
        if (!fs.existsSync(TEMP_PATH)) {
            throw new Error("Temperature file not found");
        }

        // Read the temperature only if cache is outdated
        if (Date.now() - lastUpdateTime > CACHE_DURATION) {
            const temp = fs.readFileSync(TEMP_PATH, "utf8").trim();
            cachedTemperature = parseFloat(temp) / 1000;
            lastUpdateTime = Date.now();
        }

        return cachedTemperature;
    } catch (error) {
        console.error("Error reading CPU temperature:", error);
        return null;
    }
};

// API endpoint
app.get("/cpu-temperature", (req, res) => {
    const temperature = getCpuTemperature();
    if (temperature === null) {
        return res.status(500).json({ error: "Could not read CPU temperature" });
    }
    res.json({ temperature });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
