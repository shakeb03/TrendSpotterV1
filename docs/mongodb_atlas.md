# MongoDB Atlas Setup Guide

This guide will walk you through setting up MongoDB Atlas for the Toronto Trendspotter project.

## Step 1: Create a MongoDB Atlas Account

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Sign up for a free account (you can use Google, GitHub, or email)
3. Complete the initial setup questionnaire (select the "Free" option when asked)

## Step 2: Create a Free Cluster

1. After signing up, you'll be prompted to create a new cluster
2. Choose the **FREE** tier (M0 Sandbox)
3. Select your preferred cloud provider (AWS, GCP, or Azure)
4. Choose a region close to Toronto (e.g., AWS N. Virginia or GCP Montreal)
5. Click "Create Cluster" (this will take a few minutes to provision)

## Step 3: Configure Database Access

1. While the cluster is being created, click on "Database Access" in the left menu
2. Click "Add New Database User"
3. Create a new user with a username and secure password
   - Choose "Password" authentication method
   - For privileges, select "Read and write to any database"
4. Click "Add User"

## Step 4: Configure Network Access

1. Click on "Network Access" in the left menu
2. Click "Add IP Address"
3. For development, you can allow access from anywhere by clicking "Allow Access From Anywhere" (not recommended for production)
   - Alternatively, add your specific IP address
4. Click "Confirm"

## Step 5: Get Your Connection String

1. Once your cluster is created, click on "Connect"
2. Select "Connect your application"
3. Choose "Node.js" as the driver and the latest version
4. Copy the connection string, which will look something like:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
   ```
5. Replace `<username>` and `<password>` with your database user credentials
6. Replace `myFirstDatabase` with `trendspotter`

## Step 6: Update Your .env File

1. Create a copy of `.env.example` named `.env` in your project root
2. Paste your connection string as the `MONGO_URI` value
3. Set `MONGO_DB_NAME` to `trendspotter`

## Step 7: Initialize the Database

1. Make sure your MongoDB Atlas cluster is fully provisioned (it should say "Active")
2. Run the database initialization script:
   ```bash
   python src/utils/initialize_db.py
   ```
3. Check the console output for any errors

## Troubleshooting

If you encounter connection issues:

1. Ensure your IP address is allowed in the Network Access settings
2. Verify that your username and password are correct in the connection string
3. Make sure you've replaced `<username>` and `<password>` with actual values
4. Check that the `retryWrites=true&w=majority` parameters are included

## Viewing Your Data

You can use the MongoDB Atlas web interface to view your data:

1. Go to your cluster and click "Collections"
2. You'll see your database and collections
3. You can browse, query, and manage your data through this interface

## Free Tier Limitations

The free tier M0 cluster includes:
- 512MB of storage
- Shared RAM
- Enough for development and small projects

When you reach about 80% capacity, consider:
1. Clearing old data
2. Creating a backup
3. Upgrading to a paid tier if needed

For this project, the free tier should be more than sufficient.