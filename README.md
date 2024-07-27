# Simple Authentication Accounting

Simple Authentication Accounting is a REST API developed using FastAPI. It provides an authentication system with features such as user registration, login, and OTP verification. The project supports optional two-factor authentication (2FA) via email OTP during registration.

The repository includes a simple mailer microservice to send emails through a REST API. This is a mock mail server, but it can be easily implemented with few additional code.

By changing environment variables, you can modify certain features, such as OTP generation. Use the `OTP_GENERATOR` environment variable to switch between `basic` and `static` generation. Change the `OTP_SENDER` variable to send OTPs via email or log them.

## API Endpoints

Domain URL: `http://localhost:8000/api/v1`

- **Registration**

  - **Endpoint**: `/signup`
  - **Method**: `POST`
  - **Description**: Allows users to create an account. Users can opt for 2FA by enabling OTP via email.

- **Login**

  - **Endpoint**: `/login`
  - **Method**: `POST`
  - **Description**: Authenticates users using their credentials. If 2FA is enabled, an OTP will be sent.

- **OTP Verification**

  - **Endpoint**: `/otp-verify`
  - **Method**: `POST`
  - **Description**: Validates the OTP sent to the user's email for accounts with 2FA enabled.

- **Test JWT**
  - **Endpoint**: `/token-verify`
  - **Method**: `GET`
  - **Description**: Returns information about the authenticated user.

## Development

### Requirements

- Docker and Docker Compose
- GNU Make

### Scripts

All scripts are defined in the `Makefile`. Run `make help` to see all available commands.

### How to Start

To start the service, run `make start`. This command builds and runs the container in detached mode. View the `core` service log by running `make logs`, or for mailer logs, run `make logs service=mailer`.

To create a migration file, run `make create-migration message=YOUR_MESSAGE`, then apply it with `make apply-migration`.

To stop the service, run `make stop`, and to remove all containers, use `make down`.

### Documentation

THe documentation is available at this link, `http://localhost:8000/docs`

### Tests

Test the service by running `make run-test`.

### Deploy

Deployment is defined but not implemented. You can build the production container image using `make build-release`, then choose to push it to a registry.
