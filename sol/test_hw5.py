import pytest
import copy
import os
from bbs import *


def test_example():
    assert 2 == 2

def test_general():
    clean_reset()
    connect("kathi", True)
    post_msg("homework 5", "it was just released!")
    post_msg("thoughts on homework 5", "it's the best one yet!")
    remove_msg(1)
    summary = print_summary()
    assert "Poster: kathi" in summary
    assert "Subject: thoughts on homework 5" in summary
    assert not "Subject: homework 5" in summary

def test_connect():
    clean_reset()
    connect("kathi", True)
    assert os.path.exists("disk")
    assert os.path.exists("disk/admin.txt")
    assert os.path.exists("disk/recycling.txt")

def test_post_msg():
    clean_reset()
    connect("kathi", True)
    post_msg("homework 5", "it was just released!")  

def test_max_messages_exception():
    clean_reset(3)
    connect("kathi", True)
    for i in range(3):
        post_msg("Testing", "Should work, no exception")
    with pytest.raises(Exception):
        post_msg("Testing", "This should give an exception")

def test_deleted_id_reused():
    clean_reset()
    connect("kathi", True)
    post_msg("Test 1", "Adding a message with ID 1")
    post_msg("Test 1", "Adding a message with ID 2")
    remove_msg(1)
    post_msg("Test 1", "Checking if the adding used is recycled, ID = 1")
    summary = print_summary()
    assert "ID: 1" in summary    

def test_remove_message_edge_1():
    #When there is only one message.
    clean_reset()
    connect("kathi", True)
    post_msg("Test 1", "Adding a message with ID 1")
    remove_msg(1)
    summary = print_summary()
    assert "ID: 1" not in summary      
    assert "Poster: Kathi" not in summary    
    assert "Subject: Test 1" not in summary 
    assert "Text: Adding a message with ID 1" not in summary 
def test_remove_message_edge_2():
    #A message in the middle.
    clean_reset()
    connect("kathi", True)
    post_msg("Test 1", "Adding a message with ID 1")
    post_msg("Test 2", "Adding a message with ID 2")
    post_msg("Test 3", "Adding a message with ID 3")
    remove_msg(2)
    summary = print_summary()
    assert "ID: 2" not in summary      
    assert "Subject: Test 2" not in summary 
    assert "Text: Adding a message with ID 2" not in summary 

def test_remove_message_edge_3():
    #A message in the end of a text file.
    clean_reset()
    connect("kathi", True)
    post_msg("Test 1", "Adding a message with ID 1")
    post_msg("Test 2", "Adding a message with ID 2")
    post_msg("Test 3", "Adding a message with ID 3")
    remove_msg(3)
    summary = print_summary()
    assert "ID: 3" not in summary      
    assert "Subject: Test 3" not in summary 
    assert "Text: Adding a message with ID 3" not in summary 

def test_different_users():
    #Makes sure that 
    clean_reset()
    connect("Kathi", True)
    post_msg("Test 1", "Adding a message with ID 1 - Kathi") 
    #soft_disconnect()
    connect("Salman", True)
    post_msg("Test 2", "Adding a message with ID 2 - Salman")   
    summary = print_summary()
    assert "Poster: Kathi"  in summary   
    assert "Poster: Salman" in summary 

def test_find_print_message():
    clean_reset(5) 
    connect("kathi", True)
    post_msg("Test Subject", "This is a test message.")
    message = find_print_msg(1)
    assert "ID: 1" in message
    assert "Poster: kathi" in message
    assert "Subject: Test Subject" in message
    assert "Text: This is a test message." in message    

def test_summary_with_search_term():
    clean_reset(5) 
    connect("kathi", True)
    post_msg("Test 1", "Adding a message with ID 1 - Kathi")
    post_msg("Test 2", "Adding a message with ID 2 - Kathi")
    summary = print_summary("Test 1")
    assert "Subject: Test 1" in summary
    assert "Text: Adding a message with ID 1 - Kathi" not in summary
    assert "Subject: Test 2" not in summary
    assert "Text: Adding a message with ID 2 - Kathi" not in summary

def test_summary_with_no_matching_term():
    clean_reset(5)  
    connect("kathi", True)
    post_msg("Test 1", "Adding a message with ID 1 - Kathi")
    summary = print_summary("Test 2")
    assert summary == ""

def test_remove_nonexistent_message():
    clean_reset(11)  
    connect("kathi", True)
    post_msg("Test 1", "Adding a message with ID 1 - Kathi")
    with pytest.raises(FileNotFoundError):  
        remove_msg(2)  

def test_update_string_id_from_recycled_after_disconection():
    clean_reset(10)  
    connect("kathi", True)
    post_msg("Test 1", "Adding a message with ID 1 - Kathi")
    post_msg("Test 2", "Adding a message with ID 2 - Kathi")    
    post_msg("Test 3", "Adding a message with ID 3 - Kathi")
    post_msg("Test 4", "Adding a message with ID 4 - Kathi")
    post_msg("Test 5", "Adding a message with ID 5 - Kathi")
    post_msg("Test 6", "Adding a message with ID 6 - Kathi")
    remove_msg(1)
    remove_msg(3)
    remove_msg(4)
    disconnect()
    connect("Elija", True)
    remove_msg(2)
    disconnect()
    connect("TA", True)
    post_msg("Test 7", "Adding a message with ID 1 - Kathi")
    summary = print_summary("Test 7")
    assert "ID: 1" in summary

def test_counter_messages_after_disconnect():
    clean_reset()  
    connect("kathi", True)
    post_msg("Test 1", "Adding a message with ID 1 - Kathi")
    post_msg("Test 2", "Adding a message with ID 2 - Kathi")    
    post_msg("Test 3", "Adding a message with ID 3 - Kathi")
    post_msg("Test 4", "Adding a message with ID 4 - Kathi")
    disconnect()
    connect("Elija", True)
    post_msg("Test 5", "Adding a message with ID 5 - Elija")
    summary = print_summary("Test 5")
    assert "ID: 5" in summary

def test_find_deleted_message_id():
    clean_reset()  
    connect("kathi", True)
    post_msg("Test 1", "Adding a message with ID 1 - Kathi")
    post_msg("Test 2", "Adding a message with ID 2 - Kathi")    
    remove_msg(1) 
    summary = print_summary("Test 1")
    assert "ID: 1" not in summary

