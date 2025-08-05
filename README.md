# Mikasa Expense Tracker

A full-stack expense tracker application built with **React**, **Vite**, **Tailwind CSS** (frontend) and **Node.js**, **Express**, **Prisma**, **PostgreSQL** (backend).

---

## Technologies Used

### Frontend

- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Router DOM](https://reactrouter.com/)
- [Lucide React](https://lucide.dev/)
- [React Phone Number Input](https://catamphetamine.gitlab.io/react-phone-number-input/)
- ESLint

### Backend

- [Node.js](https://nodejs.org/)
- [Express](https://expressjs.com/)
- [Prisma ORM](https://www.prisma.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [JWT](https://jwt.io/)
- [Bcrypt](https://www.npmjs.com/package/bcryptjs)
- [Nodemailer](https://nodemailer.com/)
- [Twilio](https://www.twilio.com/) (for SMS)
- [Helmet](https://helmetjs.github.io/)
- [Morgan](https://www.npmjs.com/package/morgan)
- [CORS](https://www.npmjs.com/package/cors)
- [Express Rate Limit](https://www.npmjs.com/package/express-rate-limit)
- dotenv

---

## Getting Started

### Prerequisites

- Node.js (v18+ recommended)
- PostgreSQL database
- Twilio account (for SMS)
- SMTP credentials (for email)

### Setup

#### 1. Clone the repository

```sh
git clone https://github.com/yourusername/mikasa-expense-tracker.git
cd mikasa-expense-tracker
```

#### 2. Install dependencies

```sh
cd backend
npm install

cd ../frontend
npm install
```

#### 3. Configure Environment Variables

- Copy `.env.example` to `.env` in both `backend/` and `frontend/` folders and fill in the required values.

#### 4. Setup Database

```sh
cd backend
npx prisma migrate dev --name init
```

#### 5. Run the Application

- **Backend:**

  ```sh
  cd backend
  npm run dev
  ```

- **Frontend:**

  ```sh
  cd frontend
  npm run dev
  ```

- The frontend will be available at [http://localhost:5173](http://localhost:5173) (default Vite port).

---

## Scripts

### Frontend

- `npm run dev` - Start Vite dev server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Backend

- `npm run dev` - Start backend with nodemon
- `npm start` - Start backend

---

## Features

- User registration and login (with email/username)
- Email and phone verification (with OTP via SMS)
- JWT-based authentication
- Secure password hashing
- Rate limiting and security best practices
- Responsive UI with Tailwind CSS


## Acknowledgements

- [Vite](https://vitejs.dev/)
- [Prisma](https://www.prisma.io/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Twilio](https://www.twilio.com/)
