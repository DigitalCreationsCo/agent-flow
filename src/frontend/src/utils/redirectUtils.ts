export const getStatusRedirect = (
    path: string,
    statusName: string,
    statusDescription: string = '',
    disableButton: boolean = false,
    arbitraryParams: string = ''
  ) => path
    // getToastRedirect(
    //   path,
    //   'status',
    //   statusName,
    //   statusDescription,
    //   disableButton,
    //   arbitraryParams
    // );
  
  export const getErrorRedirect = (
    path: string,
    errorName: string,
    errorDescription: string = '',
    disableButton: boolean = false,
    arbitraryParams: string = ''
  ) => path
    // getToastRedirect(
    //   path,
    //   'error',
    //   errorName,
    //   errorDescription,
    //   disableButton,
    //   arbitraryParams
    // );