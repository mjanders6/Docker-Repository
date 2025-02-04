const express = require("express");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 3000;

// Function to read CPU temperature from system files
const getCpuTemperature = () => {
    try {
        const tempPath = "/sys/class/thermal/thermal_zone0/temp";
        if (!fs.existsSync(tempPath)) {
            throw new Error("Temperature file not found");
        }

        const temp = fs.readFileSync(tempPath, "utf8").trim();
        return parseFloat(temp) / 1000; // Convert from millidegrees to Celsius
    } catch (error) {
        console.error("Error reading CPU temperature:", error);
        return null;
    }
};

app.get("/cpu-temperature", (req, res) => {
    const temperature = getCpuTemperature();
    if (temperature == null) {
        res.status(500).json({ error: "Failed to retrieve CPU temperature" });
    }
    res.json({ temperature });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
