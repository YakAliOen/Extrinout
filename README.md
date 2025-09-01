# ExTrInOut
#### Video Demo:  <https://youtu.be/z-uLdpu9ocw>
#### Description: Expense Tracker

#### Introduction:
ExTrInOut or Extrinout is an expense tracker. Its simplicity and features made it just right for anyone looking for a method to list down their expenses for daily use or any other more professional use. In fact, I made this program so that I would be able to track my daily expenses and my organising expenses from holding a TedX conference and a Model United Nations. I have adapted the files from Week 9's Problem Set Finance into this Week 10's Final Project, and one noticeable peculiarity of Extrinout compared to other expense trackers is the use of accounts. The usual approach of other expense trackers is to have the ability to sort neatly, instead, the accounts feature available in Extrinout could possibly be used to separate the expenses of different projects the users has-in my case it's daily, TedX conference, Model United Nations. At the same time, it opens the possibility to allow parents to monitor their children's expenses using the accounts feature-or similar approaches.

#### helpers.py & app.py:
I worked on this project with the mindset of working on what is hidden and slowly working towards what is seen. So before I start on app.py, I made sure that helpers.py is adjusted correctly for an expense tracker residing in Indonesia by removing entirely the lookup function and altering the usd function into idr function. Afterwards, I started altering the app.py with removing the quote route and function, and updating the buy and sell route and functions into add_expenses and delete_expenses respectively. The add_expenses route and function requests amount (value of expense), category (e.g. tax, food, pencils, etc), date (not of registered but of the expense itself) which will all be appended into the database's table (extrinout.db and expenses respectively). The delete_expenses route and function selects required information from expenses such as: id, amount, category, and date. Where all of these will be passed onto the html to display a drop down list of available expenses the user wishes to delete (deleted expense will also be removed from history). Then I altered the history route and function to get a sorting parameter from the URL, validating sorting options, and finally fetching expenses from the database according to selected sorting. Finally, I've modified the index route and function to display the total expenses sorted by category and ordered by last updated date.

#### extrinout.db:
I completely removed finance.db and made a new database, extrinout.db with 2 new and fresh tables-users and expenses. The users table contains id (as primary key), username, and hash. The expenses table consists of id (as primary key), user_id (as a foreign key referencing id in users), amount, category, and date.

#### layout.html:
Finance's layout is then  modified to refer to ExTrInOut Expense Tracker and to refer to the newly updated routes and templates. I've also implemented a small detail/feature of having the user's username displayed behind/before the logout button (only when the user is logged in).

#### add_expenses.html:
Reusing buy.html for add_expenses.html helps with formatting. All that was needed to be done was to rename the requests for amount and category while also adding the request for date.

#### delete_expenses.html:
Modifying sell.html into delete_expenses was the same work to add_expenses. All that was done was for it to request the user to select the expense they would like to delete from a drop down list of their expenses in detail.

#### history.html:
I added sorting buttons to improve usability, allowing users to organize expenses by amount, category, or date. These buttons pass sorting parameters to the history route, which processes and returns the sorted data for display. This feature makes tracking expenses more efficient and user-friendly.

#### Conclusion:
One noticeable peculiarity of ExTrInOut compared to other expense trackers is the use of accounts. Most expense trackers primarily focus on sorting expenses neatly by category. However, I chose to implement an accounts feature to provide greater flexibility in managing multiple financial contexts. In my case, I use separate accounts for daily expenses, a TEDx conference, and Model United Nations, ensuring that each financial aspect remains distinct. This design choice was deliberate, as it allows users to track expenses across different projects without mixing them into a single pool. Additionally, the accounts feature introduces potential use cases beyond personal finance—such as enabling parents to monitor their children’s spending habits. While some may argue that sorting alone is sufficient, I found that adding accounts enhances organization and adaptability. By integrating this feature, ExTrInOut offers a unique approach to expense tracking that goes beyond conventional methods, catering to diverse financial needs.
