const express = require("express");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 3000;

app.get("/cpu-temperature", async (req, res) => {
    try {
        const tempPath = "/sys/class/thermal/thermal_zone0/temp";
        if (!fs.existsSync(tempPath)) {
            return res.status(500).json({ error: "Temperature file not found" });
        }

        const temp = fs.readFileSync(tempPath, "utf8").trim();
        const temperature = parseFloat(temp) / 1000; // Convert from millidegrees to Celsius

        res.json({ temperature });
    } catch (error) {
        res.status(500).json({ error: "Failed to retrieve CPU temperature" });
    }
});

// Route to get CPU temperature and humidity
app.get("/environment", async (req, res) => {
    try {
        const temperature = getCpuTemperature();
        const sensors = await si.dhtSensors(); // Get humidity if available
        const humidity = sensors?.main?.humidity || "N/A"; // If no sensor, return N/A

        res.json({ temperature, humidity });
    } catch (error) {
        res.status(500).json({ error: "Failed to retrieve environmental data" });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
