// server.js
require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const University = require('./universityModel');

const app = express();
app.use(express.json());
app.use(cors());

// --- 1. CONNECT TO MONGODB ---
mongoose.connect(process.env.MONGO_URI)
    .then(() => console.log('✅ Connected to MongoDB Atlas'))
    .catch((err) => console.error('❌ MongoDB Connection Error:', err));

// --- 2. API ROUTES ---

// GET: SPECIAL EXPORT FOR UNITY (Returns data wrapped in { "universities": [...] })
app.get('/api/unity-export', async (req, res) => {
    try {
        const allUniversities = await University.find();
        // Wrap result to match Unity's expected ApiResponse class
        res.json({ universities: allUniversities });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// GET: Fetch all universities (For your web dashboard/admin panel)
app.get('/api/universities', async (req, res) => {
    try {
        const unis = await University.find();
        res.json(unis);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// POST, PUT, DELETE routes for management are also defined here
// (See the code provided in the previous turn for completeness)

// --- 3. START SERVER ---
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
