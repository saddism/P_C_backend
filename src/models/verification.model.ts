export interface Verification {
  id: number;
  userId: number;
  code: string;
  expiresAt: Date;
  createdAt: Date;
}
