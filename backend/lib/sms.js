const twilio = require('twilio');

const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

const sendSMS = async ({ to, message }) => {
  try {
    await client.messages.create({
      body: message,
      from: process.env.TWILIO_PHONE_NUMBER,
      to,
    });
  } catch (error) {
    console.error('SMS sending failed:', error);
    throw new Error('Failed to send SMS');
  }
};

module.exports = { sendSMS };