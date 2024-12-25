import { UseMutationResult } from "@tanstack/react-query";
import { useMutationFunctionType, Users } from "../../../../types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import { Subscription } from "@/types/billing";

type IPostAddSubscription = {
  subscription: Subscription
}

export const usePostAddSubscription: useMutationFunctionType<undefined, any> = (
  options?,
) => {
  const { mutate } = UseRequestProcessor();

  const postAddSubscriptionFn = async (
    payload: IPostAddSubscription,
  ): Promise<any> => {
    const res = await api.post<any>(`${getURL("SUBSCRIPTIONS")}/store`, {
      subscription: payload.subscription,
    });
    return res.data;
  };

  const mutation: UseMutationResult = mutate(
    ["usePostAddSubscription"],
    postAddSubscriptionFn,
    options,
  );

  return mutation;
};
