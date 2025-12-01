// server.js
require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const University = require('./universityModel');

const app = express();

// 1. CORS MUST COME FIRST (Move this to the top)
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'x-api-key']
}));

// 2. Handle Preflight Requests immediately
app.options(/(.*)/, cors());

// 3. Body Parser comes AFTER CORS
app.use(express.json());


// --- 1. CONNECT TO MONGODB ---
mongoose.connect(process.env.MONGO_URI)
    .then(() => console.log('✅ Connected to MongoDB Atlas'))
    .catch((err) => console.error('❌ MongoDB Connection Error:', err));

// --- 2. SECURITY MIDDLEWARE ---
const verifyApiKey = (req, res, next) => {
    const userKey = req.headers['x-api-key'];
    const serverKey = process.env.ADMIN_API_KEY;

    if (!userKey || userKey !== serverKey) {
        return res.status(403).json({ message: "⛔ Access Denied: Invalid API Key" });
    }
    next();
};

// --- 3. API ROUTES ---

// Public Routes
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

// Secured Routes
app.post('/api/universities', verifyApiKey, async (req, res) => {
    const uni = new University(req.body);
    try {
        const newUni = await uni.save();
        res.status(201).json(newUni);
    } catch (err) {
        res.status(400).json({ message: err.message });
    }
});

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