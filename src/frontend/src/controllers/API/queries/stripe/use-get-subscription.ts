import { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import { Subscription, SubscriptionWithProduct } from "@/types/billing";

export const useGetSubscription: useQueryFunctionType<string | undefined, SubscriptionWithProduct | null> = (
  subscriptionId?: string,
  options?, 
) => {
  const { query } = UseRequestProcessor();

  const getSubscription = async () => {
    if (!subscriptionId) {
      return null;
    }

    try {
      const response = await api.get<SubscriptionWithProduct>(
        `${getURL("SUBSCRIPTION")}/${subscriptionId}`
      );
      return response["data"];
    } catch (error: any) {
      console.error("Error fetching subscription:", error);
      if (error.response) {
        console.error("Response data:", error.response.data);
        console.error("Response status:", error.response.status);
        throw new Error(error.response.data.detail || "Failed to fetch subscription");
      } else if (error.request) {
        console.error("No response received:", error.request);
        throw new Error("No response received from server");
      } else {
        console.error("Error setting up request:", error.message);
        throw new Error("Error setting up request");
      }
    }
  };

  const queryResult = query(
    ["useGetSubscription", subscriptionId], 
    getSubscription,
    {
      enabled: !!subscriptionId,
      ...options,
    }
  );

  return queryResult;
};
