def get_arg(args,key,index=0,default=""):
    return args.get(key)[index] if args.get(key) else default