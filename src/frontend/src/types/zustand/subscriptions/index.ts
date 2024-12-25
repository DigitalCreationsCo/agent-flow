import { Subscription } from "@/types/billing";
import { Product } from "@/types/billing";
import { Price } from "@/types/billing";

export type subscriptionsStoreType = {
  subscription: Subscription | null;
  subscriptions: Subscription[];
  products: Product[];
  prices: Price[];
  setSubscriptions: (subscriptions: Subscription[]) => void;
  setProducts: (products: Product[]) => void;
  setPrices: (prices: Price[]) => void;
  setSubscription: (subscription: Subscription) => void;
};
