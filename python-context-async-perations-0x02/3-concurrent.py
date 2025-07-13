"""
Concurrent Asynchronous Database Queries
"""

import asyncio
import aiosqlite


async def async_fetch_users():
    """
    Asynchronously fetch all users from the database
    
    Returns:
        list: All user records from the users table
    """
    async with aiosqlite.connect('users.db') as db:
        print("Fetching all users...")
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        print(f"Retrieved {len(users)} users")
        return users


async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database
    
    Returns:
        list:  User records where age > 40
    """
    async with aiosqlite.connect('users.db') as db:
        print("Fetching users odler than 40...")
        age_param = 40
        cursor = await db.execute("SELECT * FROM users WHERE age > ?" , (age_param,))
        older_users = await cursor.fetchall()
        print(f"Retrieved {len(older_users)} users older than 40")
        return older_users


async def fetch_concurrently():
    """
    Execute both database queries concurrently using asyncio.gather
    
    Returns:
        tuple: Results from both queries (all_users, older_users)
    """
    print("Starting concurrent database queries...")
    
    # execute both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    print("\nConcurrent queries completed!")
    
    # show results
    print("\n" + "-"*65)
    print("ALL USERS:")
    print("-"*65)
    for user in all_users:
        print(user)
    
    print("\n" + "-"*65)
    print("USERS OLDER THAN 40:")
    print("-"*65)
    for user in older_users:
        print(user)
    
    return all_users, older_users


def main():
    """
    Main function to run the concurrent fetch operation
    """
    # run the concurrent fetch using asyncio.run
    asyncio.run(fetch_concurrently())


if __name__ == "__main__":
    main()