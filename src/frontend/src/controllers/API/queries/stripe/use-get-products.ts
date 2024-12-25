import { useQueryFunctionType } from "@/types/api";
import { api } from "@/controllers/API/api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import { ProductWithPrices } from "@/types/billing";

export const useGetProducts: useQueryFunctionType<undefined, ProductWithPrices[]> = (
  options?,
) => {
  const { query } = UseRequestProcessor();

  const getProducts = async () => {
    try {
      console.log("useGetProducts url ", getURL("PRODUCTS"));
      const response = await api.get<ProductWithPrices[]>(`${getURL("PRODUCTS")}`);
      return response["data"];
    } catch (error: any) {
      console.error("Error fetching products:", error);
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error("Response data:", error.response.data);
        console.error("Response status:", error.response.status);
        throw new Error(error.response.data.detail || "Failed to fetch products");
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

  const queryResult = query(["useGetProducts"], getProducts, {
    ...options,
  });

  return queryResult;
};
