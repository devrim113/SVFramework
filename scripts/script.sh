#!/bin/bash

# Ask for username
read -p "Enter username: " username

# Ask for password (hide input)
read -p "Enter password: " password

# Ask for server
read -p "Enter server: " server

# Echo back the inputs
echo "Username: $username"
echo "Password: $password"
echo "Server: $server"