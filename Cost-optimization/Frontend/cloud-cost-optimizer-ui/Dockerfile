# Step 1: Use the official Node.js image as a base image
FROM node:16-alpine

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy package.json and package-lock.json for dependency installation
COPY package*.json ./

# Step 4: Install the dependencies
RUN npm install

# Step 5: Copy the rest of the app's source code
COPY . .

# Step 6: Build the app
RUN npm run build

# Step 7: Install a simple web server to serve the app
RUN npm install -g serve

# Step 8: Serve the app on port 3000
CMD ["serve", "-s", "build", "-l", "3000"]

# Expose port 3000
EXPOSE 3000

