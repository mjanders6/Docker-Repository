const express = require('express');
const fs = require('fs');

const app = express();
const PORT = 3000;
const TEMP_FILE = '/sys/class/thermal/thermal_zone0/temp';
const HOST_FILE = '/etc/hostname';

function getCPUTemperature() {
    try {
        const tempData = fs.readFileSync(TEMP_FILE, 'utf8');
        const tempCelsius = parseFloat(tempData) / 1000;
        return tempCelsius;
    } catch (error) {
        console.error('Error reading CPU temperature:', error);
        return null;
    }
}

app.get('/cpu-temperature', (req, res) => {
    const temp = getCPUTemperature();
    const hostData = fs.readFileSync(HOST_FILE, 'utf8');

    if (temp !== null) {
        res.json({ host: hostData, temperature: temp, unit: 'Celsius'});
    } else {
        res.status(500).json({ error: 'Unable to read CPU temperature' });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
