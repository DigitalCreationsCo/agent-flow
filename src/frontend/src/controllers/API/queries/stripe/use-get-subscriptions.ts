import { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import { Subscription } from "@/types/billing";

export const useGetSubscriptions: useQueryFunctionType<undefined, Subscription> = (
  options?, 
) => {
  const { query } = UseRequestProcessor();

  const getSubscriptions = async () => {
    const response = await api.get<Subscription[]>(`${getURL("SUBSCRIPTIONS")}`);
    return response["data"];
  };

  const queryResult = query(["useGetSubscriptions"], getSubscriptions, {
    ...options,
  });

  return queryResult;
};
