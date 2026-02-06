/**
 * NextAuth.js v5 Configuration Template
 * OAuth Authentication Setup with Google, Facebook, and Apple
 *
 * Usage:
 * 1. Copy this file to src/lib/auth.ts
 * 2. Install dependencies: npm install next-auth @auth/prisma-adapter bcryptjs
 * 3. Set environment variables in .env.local or hosting provider
 * 4. Import and use in your app
 */

import NextAuth from "next-auth"
import { PrismaAdapter } from "@auth/prisma-adapter"
import CredentialsProvider from "next-auth/providers/credentials"
import GoogleProvider from "next-auth/providers/google"
import FacebookProvider from "next-auth/providers/facebook"
import AppleProvider from "next-auth/providers/apple"
import bcrypt from "bcryptjs"
import { prisma } from "./prisma" // Adjust path as needed

export const { handlers, auth, signIn, signOut } = NextAuth({
  // Database adapter for persisting users and sessions
  adapter: PrismaAdapter(prisma),

  // Session strategy - JWT recommended for serverless
  session: {
    strategy: "jwt",
  },

  // Custom pages
  pages: {
    signIn: "/auth/signin",
    error: "/auth/signin", // Redirect to signin on error
  },

  providers: [
    // Google OAuth
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code",
        },
      },
    }),

    // Facebook OAuth
    FacebookProvider({
      clientId: process.env.FACEBOOK_CLIENT_ID || "",
      clientSecret: process.env.FACEBOOK_CLIENT_SECRET || "",
    }),

    // Apple OAuth (optional)
    AppleProvider({
      clientId: process.env.APPLE_ID || "",
      clientSecret: process.env.APPLE_SECRET || "",
    }),

    // Email/Password Credentials (optional)
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Email and password required")
        }

        const user = await prisma.user.findUnique({
          where: { email: credentials.email as string },
        })

        if (!user) {
          throw new Error("No user found with this email")
        }

        // Verify password if user has one
        if (user.password) {
          const isValidPassword = await bcrypt.compare(
            credentials.password as string,
            user.password
          )
          if (!isValidPassword) {
            throw new Error("Invalid password")
          }
        } else {
          // User signed up with OAuth, no password set
          throw new Error("Please sign in with your social account")
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          image: user.image,
        }
      },
    }),
  ],

  callbacks: {
    // JWT callback - add custom data to token
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id
      }
      // Store provider info for potential use
      if (account) {
        token.provider = account.provider
      }
      return token
    },

    // Session callback - expose token data to client
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
      }
      return session
    },

    // Sign-in callback - control who can sign in
    async signIn({ user, account, profile }) {
      // Allow OAuth sign-ins
      if (account?.provider === "google" ||
          account?.provider === "facebook" ||
          account?.provider === "apple") {
        return true
      }
      // Allow credentials sign-in
      if (account?.provider === "credentials") {
        return true
      }
      return true
    },
  },

  events: {
    // Create user event - initialize user data
    async createUser({ user }) {
      // Example: Initialize credits or settings for new users
      if (user.id) {
        // Add your user initialization logic here
        console.log(`New user created: ${user.email}`)
      }
    },
  },
})

/**
 * Hash a password using bcrypt
 */
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12)
}

/**
 * Verify a password against a hash
 */
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash)
}
