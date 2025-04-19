/**
 * Format a date for display
 */
export const formatDate = (date: Date): string => {
    const options: Intl.DateTimeFormatOptions = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    };
    
    return date.toLocaleDateString('en-CA', options);
  };
  
  /**
   * Format a date and time for display
   */
  export const formatDateTime = (date: Date): string => {
    const options: Intl.DateTimeFormatOptions = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    return date.toLocaleDateString('en-CA', options);
  };
  
  /**
   * Format a price for display
   */
  export const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: 'CAD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(price);
  };
  
  /**
   * Truncate text to a certain length
   */
  export const truncateText = (text: string, maxLength: number = 100): string => {
    if (!text || text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };
  
  /**
   * Get a readable relative time (e.g., "2 days ago", "5 minutes ago")
   */
  export const getRelativeTime = (date: Date): string => {
    const now = new Date();
    const diffInMilliseconds = now.getTime() - date.getTime();
    
    const minute = 60 * 1000;
    const hour = minute * 60;
    const day = hour * 24;
    const week = day * 7;
    const month = day * 30;
    const year = day * 365;
    
    if (diffInMilliseconds < minute) {
      return 'just now';
    } else if (diffInMilliseconds < hour) {
      const minutes = Math.floor(diffInMilliseconds / minute);
      return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInMilliseconds < day) {
      const hours = Math.floor(diffInMilliseconds / hour);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (diffInMilliseconds < week) {
      const days = Math.floor(diffInMilliseconds / day);
      return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (diffInMilliseconds < month) {
      const weeks = Math.floor(diffInMilliseconds / week);
      return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    } else if (diffInMilliseconds < year) {
      const months = Math.floor(diffInMilliseconds / month);
      return `${months} month${months > 1 ? 's' : ''} ago`;
    } else {
      const years = Math.floor(diffInMilliseconds / year);
      return `${years} year${years > 1 ? 's' : ''} ago`;
    }
  };