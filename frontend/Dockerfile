FROM node:18-alpine

WORKDIR /app

# Copy dependency files first to leverage Docker layer caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY . .

# Expose the React development server port
EXPOSE 3000

# Start the React application
# Environment variables starting with REACT_APP_ will be picked up here
CMD ["npm", "start"]