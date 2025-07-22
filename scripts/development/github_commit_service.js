
const express = require('express');
const axios = require('axios');
const jwt = require('jsonwebtoken');
const fs = require('fs');
const app = express();
app.use(express.json());

// === CONFIGURATION ===
const APP_ID = 'your_app_id';  // Replace with your GitHub App ID
const INSTALLATION_ID = 'your_installation_id';  // Replace with your GitHub App Installation ID
const PRIVATE_KEY = fs.readFileSync('private-key.pem', 'utf8');  // GitHub App private key

const REPO_OWNER = 'kor-ai';
const REPO_NAME = 'kor-ai-core';

// === JWT GENERATION ===
function generateJWT() {
    const now = Math.floor(Date.now() / 1000);
    const payload = {
        iat: now,
        exp: now + (10 * 60),
        iss: APP_ID
    };
    return jwt.sign(payload, PRIVATE_KEY, { algorithm: 'RS256' });
}

// === ROUTE TO COMMIT A FILE ===
app.post('/github/commit', async (req, res) => {
    const { filePath, content, message } = req.body;

    try {
        const jwtToken = generateJWT();

        const tokenResp = await axios.post(
            `https://api.github.com/app/installations/${INSTALLATION_ID}/access_tokens`,
            {},
            {
                headers: {
                    Authorization: `Bearer ${jwtToken}`,
                    Accept: 'application/vnd.github+json'
                }
            }
        );

        const ghToken = tokenResp.data.token;

        const encodedContent = Buffer.from(content).toString('base64');

        await axios.put(
            `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`,
            {
                message: message,
                content: encodedContent
            },
            {
                headers: {
                    Authorization: `token ${ghToken}`,
                    Accept: 'application/vnd.github+json'
                }
            }
        );

        res.status(200).send({ status: 'success', filePath });
    } catch (error) {
        console.error(error.response?.data || error.message);
        res.status(500).send({ status: 'error', message: error.message });
    }
});

// === START SERVER ===
app.listen(3001, () => {
    console.log('Commit service running on port 3001');
});
