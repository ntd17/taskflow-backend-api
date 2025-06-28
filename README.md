# TaskFlow Backend

This is the backend API for TaskFlow, a Trello-like collaborative Kanban board application for mobile apps.

## Features

- User registration and login with JWT authentication
- Boards with lists (columns) and cards (tasks)
- Real-time collaboration with board members
- CRUD operations for boards, lists, and cards
- Board sharing and member management
- OpenAPI/Swagger documentation
- Containerized with Docker and Docker Compose
- PostgreSQL database with SQLAlchemy ORM

## Requirements

- Docker and Docker Compose installed

## Setup and Run

1. Clone the repository

2. Build and start the services with Docker Compose:

```bash
docker-compose up --build
```

This will start the PostgreSQL database and the Flask backend API on port 5000.

3. The API will be accessible at: `http://localhost:5000`

## API Documentation

Swagger UI is available at:

```
http://localhost:5000/
```

## Environment Variables

- `SECRET_KEY`: Flask secret key (default: `supersecretkey`)
- `JWT_SECRET_KEY`: JWT secret key (default: `jwt-secret-string`)
- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://taskflow:changeme@db:5432/taskflow`)

## Database Migrations

To run database migrations (requires Flask-Migrate):

```bash
docker-compose exec backend flask db init
docker-compose exec backend flask db migrate
docker-compose exec backend flask db upgrade
```

## Example Requests

- Register:

```bash
POST /api/auth/register
{
  "username": "user1",
  "email": "user1@example.com",
  "password": "password123"
}
```

- Login:

```bash
POST /api/auth/login
{
  "username": "user1",
  "password": "password123"
}
```

- Create Board:

```bash
POST /api/boards
Authorization: Bearer <access_token>
{
  "title": "My Board"
}
```

- Invite User to Board:

```bash
POST /api/boards/<board_id>/invite
Authorization: Bearer <access_token>
{
  "email_or_username": "user2@example.com"
}
```

- List Board Members:

```bash
GET /api/boards/<board_id>
Authorization: Bearer <access_token>
```
(The response includes a `members` field listing all members)

- Add Member by Email:

```bash
POST /api/boards/<board_id>/members
Authorization: Bearer <access_token>
{
  "email": "user3@example.com"
}
```

- Remove Member:

```bash
DELETE /api/boards/<board_id>/members/<user_id>
Authorization: Bearer <access_token>
```

## Permissions Model

- Any board member can invite, add, or remove other members from the board.
- There is currently no owner/admin role; all members have equal permissions for member management.

## Notes

- All endpoints requiring authentication expect a JWT token in the `Authorization` header.
- The backend is designed to be consumed by a mobile app client.

## License

MIT License
