# Use Node.js 18 as the base image
FROM node:18
# Install Jest globally
RUN npm install -g jest
# Create a Jest configuration file
RUN echo "module.exports = { testMatch: ['**/tests/**/*.test.js'], testEnvironment: 'node', verbose: true };" > /jest.config.js
# Set a working directory (optional, since we use absolute paths)
WORKDIR /app
# Run Jest with the config file and output to results.json
CMD ["jest", "--config=/jest.config.js", "--json", "--outputFile=/results/results.json"]