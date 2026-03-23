import { useState, useRef, useEffect } from 'react'

interface ReferralContact {
  name: string
  company: string
  application_id: number
}

interface ReferralPopoverProps {
  contacts: ReferralContact[]
}

export function ReferralPopover({ contacts }: ReferralPopoverProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    if (open) document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  return (
    <div className="referral-popover-container" ref={ref}>
      <button className="referral-popover-trigger" onClick={() => setOpen(!open)}>
        View all referrals →
      </button>
      {open && (
        <div className="referral-popover" data-testid="referral-popover">
          {contacts.map((c) => (
            <div key={c.application_id} className="referral-popover-item">
              <span className="referral-name">{c.name}</span>
              <span className="referral-company">{c.company}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
