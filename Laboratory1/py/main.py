from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement
import hmac
import hashlib

# Configs
cassandra_port = '127.0.0.1'
key_space_name = 'lecturebot'
secret_key = "8581b093484655e699dd47ea78bb0d67e4e2aa9928e29a2653f232663f620dc5" #Password Salt
###


# User defined functions
def get_password_hash(salt, password):
    return hmac.new(bytes(salt, 'UTF-8'), msg=bytes(password, 'UTF-8'), digestmod=hashlib.sha256).hexdigest().upper()
###


# Defined queries

# INSERT
insert_new_user_with_new_lecture_query = SimpleStatement(
    """
    INSERT INTO user_lectures(login, password_hash, password_salt, role, resources, 
                                         lecture_id, lecture_header, lecture_content, lecture_raw_view)
    VALUES (%s, textAsBlob(%s), textAsBlob(%s), {
	    "name": %s, 
	    "priority": %s, 
	    "allowed_self_crud": %s,
	    "allow_unlimited_serialization": %s,
	    "allow_role_grant": %s
    }, %s, %s, %s, %s, %s);
    """,
    consistency_level=ConsistencyLevel.ONE)

insert_new_lecture_to_existing_user_query = SimpleStatement(
    """
    INSERT INTO user_lectures (login, lecture_id, lecture_header, lecture_content, lecture_raw_view)
    VALUES (%s, %s, %s, %s, %s);
    """,
    consistency_level=ConsistencyLevel.ONE)

insert_new_component_with_new_resource_query = SimpleStatement(
    """
    INSERT INTO resource_components (url, description, times_visited,
                                     component_id, component_tag, component_attributes, component_inner)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s);
    """,
    consistency_level=ConsistencyLevel.ONE)

insert_new_component_to_existing_resource_query = SimpleStatement(
    """
    INSERT INTO user_lectures (url, component_id, component_tag, component_attributes, component_inner)
    VALUES (%s, %s, %s, %s, %s);
    """,
    consistency_level=ConsistencyLevel.ONE)

# UPDATE
update_user_data_structure_user_lectures_query = SimpleStatement(
    """
    UPDATE user_lectures
    SET role = {
        "name": 'Admin', 
        "priority": 1, 
        "allowed_self_crud": true,
        "allow_unlimited_serialization": true,
        "allow_role_grant": true
    }
    WHERE login = %s;
    """,
    consistency_level=ConsistencyLevel.ONE)

update_static_user_lectures_query = SimpleStatement(
    """
    UPDATE user_lectures
    SET password_hash = textAsBlob(%s),
    password_salt = textAsBlob(%s)
    WHERE login = %s;
    """,
    consistency_level=ConsistencyLevel.ONE)

update_regular_user_lectures_query = SimpleStatement(
    """
    UPDATE user_lectures
    SET lecture_header=%s
    WHERE login = %s AND lecture_id = %s;
    """,
    consistency_level=ConsistencyLevel.ONE)

update_static_resource_component_query = SimpleStatement(
    """
    UPDATE resource_components
    SET times_visited = %s
    WHERE url = %s;
    """,
    consistency_level=ConsistencyLevel.ONE)

update_regular_resource_component_query = SimpleStatement(
    """
    UPDATE resource_components
    SET component_tag = %s
    WHERE url = %s AND component_id = %s;
    """,
    consistency_level=ConsistencyLevel.ONE)

# CUSTOM

set_premium_plan_query = SimpleStatement(
    """
    UPDATE user_lectures
    SET role = {
        "name": 'Super User', 
        "priority": 2, 
        "allowed_self_crud": true,
        "allow_unlimited_serialization": true,
        "allow_role_grant": false
    }
    WHERE login = %s
    """,
    consistency_level=ConsistencyLevel.ONE)

get_raw_resource_query = SimpleStatement(
    """
    SELECT component_inner FROM resource_components
    WHERE url = %s;
    """,
    consistency_level=ConsistencyLevel.ONE)

get_all_serialized_lectures_query = SimpleStatement(
    """
    SELECT lecture_header, lecture_content FROM user_lectures
    WHERE login = %s;
    """,
    consistency_level=ConsistencyLevel.ONE)

set_counter_to_new_resource_query = SimpleStatement(
    """
    UPDATE lecturebot.resource_components
    SET times_visited = 1
    WHERE url = %s;
    """,
    consistency_level=ConsistencyLevel.ONE)

# DELETE

delete_user_lecture_query = SimpleStatement(
    """
    DELETE FROM user_lectures
    WHERE login = %s AND lecture_id = %s;
    """,
    consistency_level=ConsistencyLevel.ONE)

delete_resource_components_query = SimpleStatement(
    """
    DELETE FROM resource_components
    WHERE url = %s AND component_id = %s;
    """,
    consistency_level=ConsistencyLevel.ONE)

###


cluster = Cluster([cassandra_port])
session = cluster.connect(key_space_name)


# Execute queries

# INSERT
session.execute(
    insert_new_user_with_new_lecture_query,
    ("linus__torvalds",
     get_password_hash(secret_key, password='linux4legends'),
     secret_key,
     "Super User", 2, True, True, False,
     {'https://en.wikipedia.org/wiki/Linux', 'https://www.techradar.com/best/best-linux-distros', 'https://www.wired.com/2012/05/torvalds-github'},
     1,
     'Main reasons why Linux is the best OS!',
     'Main reasons why Linux is the best OS: 1) In Linux user has access to the source code of kernel and alter the code according to his need. It has its own advantages like bugs in OS will fix at a rapid pace and disadvantages like developers may take advantage of any weakness in OS if they found. 2) Linux has various distributions which are highly customizable based on user needs. 3) In Linux with GPL- Licensed operating system, users are free to modify the software, can re-use in any number of systems and even they can sell the modified version. 4) Linux is more secure than windows where hackers or developers of viruses will find difficult to break through Linux. 5) All software in Linux is free!',
     [{
		 'header': 'Main reasons why Linux is the best OS: ',
		 'p': '1) In Linux user has access to the source code of kernel and alter the code according to his need. It has its own advantages like bugs in OS will fix at a rapid pace and disadvantages like developers may take advantage of any weakness in OS if they found.'
	 }, {
		 'p': '2) Linux has various distributions which are highly customizable based on user needs.'
	 }, {
		 'p': '3) In Linux with GPL- Licensed operating system, users are free to modify the software, can re-use in any number of systems and even they can sell the modified version.'
	 }, {
		 'p': '4) Linux is more secure than windows where hackers or developers of viruses will find difficult to break through Linux.'
	 }, {
		 'p': '5) All software in Linux is free!'
	 }])
)


session.execute(
    insert_new_user_with_new_lecture_query,
    ("admin",
     get_password_hash(secret_key, password='admin'),
     secret_key,
     "Admin", 1, True, True, True,
     {'http://cassandra.apache.org/', 'https://docs.datastax.com/en/archived/cql/3.3/cql/cqlIntro.html', 'https://www.techighness.com/post/nosql-one-to-many-relation-bound-unbound-examples/'},
     1,
     'NoSQL and Cassandra',
     'What is Cassandra? The Apache Cassandra database is the right choice when you need scalability and high availability without compromising performance. Linear scalability and proven fault-tolerance on commodity hardware or cloud infrastructure make it the perfect platform for mission-critical data. Cassandra’s support for replicating across multiple datacenters is best-in-class, providing lower latency for your users and the peace of mind of knowing that you can survive regional outages.',
     [{
		'h3': 'What is Cassandra?',
		'p': 'The Apache Cassandra database is the right choice when you need scalability and high availability without compromising performance. Linear scalability and proven fault-tolerance on commodity hardware or cloud infrastructure make it the perfect platform for mission-critical data. Cassandra’s support for replicating across multiple datacenters is best-in-class, providing lower latency for your users and the peace of mind of knowing that you can survive regional outages.'
	 }])
)


session.execute(
    insert_new_lecture_to_existing_user_query,
    ("linus__torvalds",
     2,
     'The Future of Open Source Is So Bright!',
     'We began by asking, "What’s the future of Open Source software from your perspective?" Here’s what they told us: "Growth": Very bright: Docker has radically changed the way OSS is consumed, and now it’s very simple to distribute OSS to a wider audience. It will continue to accelerate and be integrated in different ways to solve problems and achieve results. Start caring about upgrades. Data shows people don’t upgrade and this results in tremendous liability. Some companies have an effort to look inside and start licensing components by hand to look at risk and to know what’s going on. Security and legal need to work together to assess risk.',
     [{
		  'h1': 'We began by asking, "What’s the future of Open Source software from your perspective?"',
		  'h3': 'Here’s what they told us:'
	  },
	  {
		  'span': '"Growth":',
		  'p': 'Very bright: Docker has radically changed the way OSS is consumed, and now it’s very simple to distribute OSS to a wider audience. It will continue to accelerate and be integrated in different ways to solve problems and achieve results. Start caring about upgrades. Data shows people don’t upgrade and this results in tremendous liability. Some companies have an effort to look inside and start licensing components by hand to look at risk and to know what’s going on. Security and legal need to work together to assess risk.'
	  }])
)


session.execute(
    insert_new_component_with_new_resource_query,
    ("https://en.wikipedia.org/wiki/Linux",
     "Wikipedia: Linux",
     2,
     1,
     'h1',
     {
         'id': 'firstHeading',
         'class': 'firstHeading',
         'lang': 'en'
     },
     'Linux')
)


session.execute(
    insert_new_component_with_new_resource_query,
    ("http://cassandra.apache.org",
     "Apache Cassandra",
     1,
     1,
     'p',
     {
         'id': 'firstHeading',
	     'class': 'firstHeading',
	     'lang': 'en'
     },
     'The Apache Cassandra database is the right choice when you need scalability and high availability without compromising performance. <a href="http://techblog.netflix.com/2011/11/benchmarking-cassandra-scalability-on.html">Linear scalability</a> and proven fault-tolerance on commodity hardware or cloud infrastructure make it the perfect platform for mission-critical data. Cassandra’s support for replicating across multiple datacenters is best-in-class, providing lower latency for your users and the peace of mind of knowing that you can survive regional outages.')
)


session.execute(
    insert_new_component_to_existing_resource_query,
    ('http://cassandra.apache.org',
     2,
     'p',
     {
         'id': 'firstHeading',
	     'class': 'firstHeading',
	     'lang': 'en'
     },
     'Linux (/ˈlɪnəks/ (About this soundlisten) LIN-əks)[9][10] is a family of open source Unix-like operating systems based on the Linux kernel,[11] an operating system kernel first released on September 17, 1991, by Linus Torvalds.[12][13][14] Linux is typically packaged in a Linux distribution. Distributions include the Linux kernel and supporting system software and libraries, many of which are provided by the GNU Project. Many Linux distributions use the word "Linux" in their name, but the Free Software Foundation uses the name GNU/Linux to emphasize the importance of GNU software, causing some controversy.[15][16] Popular Linux distributions[17][18][19] include Debian, Fedora, and Ubuntu. Commercial distributions include Red Hat Enterprise Linux and SUSE Linux Enterprise Server. Desktop Linux distributions include a windowing system such as X11 or Wayland, and a desktop environment such as GNOME or KDE Plasma 5. Distributions intended for servers may omit graphics altogether, or include a solution stack such as LAMP. Because Linux is freely redistributable, anyone may create a distribution for any purpose. Linux was originally developed for personal computers based on the Intel x86 architecture, but has since been ported to more platforms than any other operating system.[20] Linux is the leading operating system on servers and other big iron systems such as mainframe computers, and the only OS used on TOP500 supercomputers (since November 2017, having gradually eliminated all competitors).[21][22][23] It is used by around 2.3 percent of desktop computers.[24][25] The Chromebook, which runs the Linux kernel-based Chrome OS, dominates the US K–12 education market and represents nearly 20 percent of sub-$300 notebook sales in the US.[26] Linux also runs on embedded systems, i.e. devices whose operating system is typically built into the firmware and is highly tailored to the system. This includes routers, automation controls, televisions,[27][28] digital video recorders, video game consoles, and smartwatches.[29] Many smartphones and tablet computers run Android and other Linux derivatives.[30] Because of the dominance of Android on smartphones, Linux has the largest installed base of all general-purpose operating systems.[31] Linux is one of the most prominent examples of free and open-source software collaboration. The source code may be used, modified and distributed—commercially or non-commercially—by anyone under the terms of its respective licenses, such as the GNU General Public License.')
)

# UPDATE
session.execute(
    update_user_data_structure_user_lectures_query,
    ('linus__torvalds')
)

session.execute(
    update_static_user_lectures_query,
    (
        get_password_hash(secret_key, 'linux4thebest'),
        secret_key,
        'linus__torvalds'
    )
)


session.execute(
    update_regular_user_lectures_query,
    (
        'Linus Torvalds: Main reasons why Linux is the best OS!',
        'linus__torvalds',
        1
    )
)


session.execute(
    update_static_resource_component_query,
    (
        5,
        'https://en.wikipedia.org/wiki/Linux'
    )
)


session.execute(
    update_regular_resource_component_query,
    (
        'a',
        'https://en.wikipedia.org/wiki/Linux',
        2
    )
)


# CUSTOM
session.execute(
    set_premium_plan_query,
    ('linus__torvalds')
)


raw_resource = session.execute(
    get_raw_resource_query,
    ('https://en.wikipedia.org/wiki/Linux')
)


serialized_lectures = session.execute(
    get_all_serialized_lectures_query,
    ('linus__torvalds')
)


session.execute(
    set_counter_to_new_resource_query,
    ('lhttps://en.wikipedia.org/wiki/Linux')
)


# DELETE
session.execute(
    delete_user_lecture_query,
    ('admin', 1)
)


session.execute(
    delete_user_lecture_query,
    ('linus__torvalds', 2)
)


session.execute(
    delete_user_lecture_query,
    ('linus__torvalds', 1)
)


session.execute(
    delete_resource_components_query,
    ('http://cassandra.apache.org', 1)
)


session.execute(
    delete_resource_components_query,
    ('https://en.wikipedia.org/wiki/Linux', 2)
)


session.execute(
    delete_resource_components_query,
    ('https://en.wikipedia.org/wiki/Linux', 1)
)
