import { create } from "zustand";
import { subscriptionsStoreType } from "@/types/zustand/subscriptions";
import { Price } from "@/types/billing";
import { Product } from "@/types/billing";
import { Subscription } from "@/types/billing";

export const useSubscriptionsStore = create<subscriptionsStoreType>((set, get) => ({
  prices: [],
  products: [],
  subscriptions: [],
  subscription: null,
  setPrices: (prices: Price[]) => {
    set({ prices });
  },
  setProducts: (products: Product[]) => {
    set({ products });
  },
  setSubscriptions: (subscriptions: Subscription[]) => {
    set({ subscriptions });
  },
  setSubscription: (subscription: Subscription) => {
    set({ subscription });
  },
}));
