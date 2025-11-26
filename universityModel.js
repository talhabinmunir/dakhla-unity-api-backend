// universityModel.js
const mongoose = require('mongoose');

// Define the inner programs structure
const ProgramSchema = new mongoose.Schema({
    programId: { type: String, required: true },
    name: { type: String, required: true },
    minRequiredPercentage: { type: Number, required: true },
    duration: { type: String },
    applicationDeadline: { type: String },
    streamTags: [String]
});

// Define the main university structure
const UniversitySchema = new mongoose.Schema({
    id: { type: String, required: true, unique: true },
    name: { type: String, required: true },
    location: { type: String },
    sector: { type: String },
    websiteUrl: { type: String },
    contactPhone: { type: String },
    contactEmail: { type: String },
    address: { type: String },
    logoUrl: { type: String },
    programs: [ProgramSchema]
});

module.exports = mongoose.model('University', UniversitySchema);
