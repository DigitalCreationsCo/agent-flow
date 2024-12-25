import { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import { Price } from "@/types/billing";

export const useGetPrices: useQueryFunctionType<undefined, Price[]> = (
  options?,
) => {
  const { query } = UseRequestProcessor();

  const getPrices = async () => {
    try {
      const response = await api.get<Price[]>(`${getURL("PRICES")}`);
      return response["data"];
    } catch (error: any) {
      console.error("Error fetching prices:", error);
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error("Response data:", error.response.data);
        console.error("Response status:", error.response.status);
        throw new Error(error.response.data.detail || "Failed to fetch prices");
      } else if (error.request) {
        // The request was made but no response was received
        console.error("No response received:", error.request);
        throw new Error("No response received from server");
      } else {
        // Something happened in setting up the request
        console.error("Error setting up request:", error.message);
        throw new Error("Error setting up request");
      }
    }
  };

  const queryResult = query(["useGetPrices"], getPrices, {
    ...options,
  });

  return queryResult;
};
