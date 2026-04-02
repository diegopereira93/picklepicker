import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap font-bold rounded-[2px] transition-colors disabled:pointer-events-none disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#000000] focus-visible:outline-offset-2",
  {
    variants: {
      variant: {
        default:
          "bg-transparent border-[2px] border-[#76b900] text-white hover:bg-[#1eaedb] hover:text-white active:bg-[#007fff] active:border-[#003eff] active:border rounded-[2px] focus-visible:bg-[#1eaedb] focus-visible:opacity-90",
        secondary:
          "bg-transparent border border-[#76b900] text-white hover:bg-[#1eaedb] hover:text-white active:bg-[#007fff] active:border-[#003eff] rounded-[2px] focus-visible:bg-[#1eaedb] focus-visible:opacity-90",
        light:
          "bg-transparent border-[2px] border-[#76b900] text-black hover:bg-[#76b900] hover:text-black active:bg-[#5a9100] active:border-[#5a9100] rounded-[2px] focus-visible:bg-[#76b900] focus-visible:opacity-90",
        compact:
          "bg-transparent border border-[#76b900] text-white hover:bg-[#1eaedb] hover:text-white rounded-[2px] tracking-[0.144px] leading-none",
        outline:
          "bg-transparent border border-[#76b900] text-white hover:bg-[#1eaedb] hover:text-white rounded-[2px]",
        ghost:
          "bg-transparent text-white hover:bg-[#1a1a1a] hover:text-white rounded-[2px]",
        destructive:
          "bg-[#e52020] text-white border-0 hover:bg-[#c01818] rounded-[2px]",
        link: "bg-transparent text-[#76b900] underline hover:text-[#3860be] p-0 h-auto",
      },
      size: {
        default: "py-[11px] px-[13px] text-[16px] font-bold leading-[1.25]",
        sm: "py-[11px] px-[13px] text-[14px] font-bold leading-[1.25]",
        lg: "py-[11px] px-[13px] text-[16px] font-bold leading-[1.25]",
        icon: "h-10 w-10 p-0",
        compact: "py-[11px] px-[13px] text-[16px] font-bold leading-none tracking-[0.144px]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
