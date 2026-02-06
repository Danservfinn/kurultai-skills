/**
 * NextAuth.js API Route Handler
 *
 * Usage:
 * 1. Create file at: src/app/api/auth/[...nextauth]/route.ts
 * 2. Copy this content
 * 3. Adjust import path to your auth.ts location
 */

import { handlers } from "@/lib/auth"

export const { GET, POST } = handlers
