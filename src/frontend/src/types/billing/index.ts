export interface ProductWithPrices extends Product {
  prices: Price[];
}
export interface PriceWithProduct extends Price {
  products: Product | null;
}
export interface SubscriptionWithProduct extends Subscription {
  prices: PriceWithProduct | null;
}

export type Price = {
  id: string;
  name: string;
  type: "one_time" | "recurring";
  price: number;
  interval: "day" | "week" | "month" | "year";
  unit_amount: number;
  currency: string;
  interval_count: number;
  trial_period_days: number;
};

export type Product = {
  id: string;
  name: string;
  description: string;
  prices: Price[];
  active: boolean | null;
  image: string | null;
  metadata: Record<string, any> | null;
};

export type Subscription = {
  cancel_at: string | null
  cancel_at_period_end: boolean | null
  canceled_at: string | null
  created: string
  current_period_end: string
  current_period_start: string
  ended_at: string | null
  id: string
  metadata: Record<string, any> | null
  price_id: string | null
  quantity: number | null
  status: SubscriptionStatus
  trial_end: string | null
  trial_start: string | null
  user_id: string
}

enum SubscriptionStatus {
  TRIALING = "trialing",
  ACTIVE = "active",
  CANCELED = "canceled",
  INCOMPLETE = "incomplete",
  INCOMPLETE_EXPIRED = "incomplete_expired",
  PAST_DUE = "past_due",
  UNPAID = "unpaid",
  PAUSED = "paused"
}