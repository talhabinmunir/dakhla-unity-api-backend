// server.js - Secured Version
require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const University = require('./universityModel');

const app = express();
app.use(express.json());
app.use(cors({
    origin: '*', // Allow all origins (GitHub Pages)
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'x-api-key']
}));

// 2. EXPLICIT PRE-FLIGHT HANDLER (Crucial for DELETE requests)
app.options('*', cors()); // Enable pre-flight across-the-board

// --- 1. CONNECT TO MONGODB ---
mongoose.connect(process.env.MONGO_URI)
    .then(() => console.log('✅ Connected to MongoDB Atlas'))
    .catch((err) => console.error('❌ MongoDB Connection Error:', err));

// --- 2. SECURITY MIDDLEWARE ---
const verifyApiKey = (req, res, next) => {
    // Get key from header
    const userKey = req.headers['x-api-key'];
    const serverKey = process.env.ADMIN_API_KEY;

    // Check if keys match
    if (!userKey || userKey !== serverKey) {
        return res.status(403).json({ message: "⛔ Access Denied: Invalid API Key" });
    }
    next();
};

// --- 3. API ROUTES ---

// PUBLIC ROUTES (Unity App & Dashboard Read-Only)
// No verifyApiKey needed here, so Unity keeps working seamlessly.

app.get('/api/unity-export', async (req, res) => {
    try {
        const allUniversities = await University.find();
        res.json({ universities: allUniversities });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

app.get('/api/universities', async (req, res) => {
    try {
        const unis = await University.find();
        res.json(unis);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// SECURED ROUTES (Dashboard Write Access)
// verifyApiKey is added as a second argument. Code runs only if key is correct.

// Add University
app.post('/api/universities', verifyApiKey, async (req, res) => {
    const uni = new University(req.body);
    try {
        const newUni = await uni.save();
        res.status(201).json(newUni);
    } catch (err) {
        res.status(400).json({ message: err.message });
    }
});

// Update University
app.put('/api/universities/:id', verifyApiKey, async (req, res) => {
    try {
        const updatedUni = await University.findOneAndUpdate(
            { id: req.params.id },
            req.body,
            { new: true }
        );
        res.json(updatedUni);
    } catch (err) {
        res.status(400).json({ message: err.message });
    }
});

// Delete University
app.delete('/api/universities/:id', verifyApiKey, async (req, res) => {
    try {
        await University.findOneAndDelete({ id: req.params.id });
        res.json({ message: 'University deleted' });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// --- 4. START SERVER ---
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));