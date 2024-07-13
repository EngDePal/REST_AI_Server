import express from 'express';
import bodyParser from 'body-parser';

const app = express();
const port = 3000;

app.use(bodyParser.json());

// Define the commands
const commands = ["EXIT", "LOG", "INFO", "LIN", "PTP", "CIRC"];

// Counter for the number of times /command is called
let commandCounter = 0;

// Define the frames
const frame = {
    a: 0,
    b: 0,
    c: 0,
    x: 300,
    y: 123,
    z: 200
};

const auxiliaryFrame = {
    a: 1,
    b: 1,
    c: 1,
    x: 301,
    y: 124,
    z: 201
};

const destination = {
    a: 2,
    b: 2,
    c: 2,
    x: 302,
    y: 125,
    z: 202
};

// Respond to /command
app.get('/command', (req, res) => {
    const currentCommand = commands[commandCounter];
    commandCounter += 1;
    if (commandCounter >= commands.length) {
        commandCounter = 0; // Reset the counter after the last command
    }
    res.json({ command: currentCommand, count: commandCounter });
});

// Respond to /frame
app.get('/frame', (req, res) => {
    const currentCommand = commands[(commandCounter - 1 + commands.length) % commands.length];
    if (currentCommand === "LIN" || currentCommand === "PTP") {
        res.json(frame);
    } else {
        res.status(400).send('Invalid command for frame request');
    }
});

// Respond to /auxiliaryFrame
app.get('/auxiliaryFrame', (req, res) => {
    const currentCommand = commands[(commandCounter - 1 + commands.length) % commands.length];
    if (currentCommand === "CIRC") {
        res.json(auxiliaryFrame);
    } else {
        res.status(400).send('Invalid command for auxiliaryFrame request');
    }
});

// Respond to /destination
app.get('/destination', (req, res) => {
    const currentCommand = commands[(commandCounter - 1 + commands.length) % commands.length];
    if (currentCommand === "CIRC") {
        res.json(destination);
    } else {
        res.status(400).send('Invalid command for destination request');
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});